#include "StationPlayerPresentationComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Camera/CameraComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

UStationPlayerPresentationComponent::UStationPlayerPresentationComponent()
{
 PrimaryComponentTick.bCanEverTick=true;
 PrimaryComponentTick.TickGroup=TG_PostPhysics;
}

void UStationPlayerPresentationComponent::BeginPlay()
{
 Super::BeginPlay();
 Character=Cast<ACharacter>(GetOwner());
 if(!Character)return;
 Camera=Character->FindComponentByClass<UCameraComponent>();
 Beam=Character->FindComponentByClass<USpotLightComponent>();
 if(!Camera || !Beam)return;
 AddTickPrerequisiteComponent(Character->GetCharacterMovement());
 HeldRoot=NewObject<USceneComponent>(Character,TEXT("HeldTorchMotion"));
 HeldRoot->SetupAttachment(Camera);HeldRoot->RegisterComponent();
 TInlineComponentArray<UStaticMeshComponent*> Parts(Character);
 for(UStaticMeshComponent* Part:Parts)
 {
  const FString Name=Part->GetName();
  if(Name.StartsWith(TEXT("Torch")) || Name.StartsWith(TEXT("Gloved")) || Name.StartsWith(TEXT("JacketSleeve")))
   Part->AttachToComponent(HeldRoot,FAttachmentTransformRules::KeepRelativeTransform);
  if(DetailedTorchMesh && Name.StartsWith(TEXT("Torch")))Part->SetHiddenInGame(true);
  // Retire the oversized spherical thumb placeholder beside the detailed casing.
  if(DetailedTorchMesh && Name.StartsWith(TEXT("GlovedThumb")))Part->SetHiddenInGame(true);
 }
 if(DetailedTorchMesh)
 {
  UStaticMeshComponent* Model=NewObject<UStaticMeshComponent>(Character,TEXT("HeldTorchDetailed"));
  Model->SetupAttachment(HeldRoot);Model->SetStaticMesh(DetailedTorchMesh);
  Model->SetRelativeLocation(FVector(16.5f,17.5f,-11));
  Model->SetCollisionProfileName(TEXT("NoCollision"));Model->SetOnlyOwnerSee(true);
  Model->SetCastShadow(false);Model->RegisterComponent();
 }
 Beam->AttachToComponent(HeldRoot,FAttachmentTransformRules::KeepRelativeTransform);
 if(Beam->LightFunctionMaterial)
 {
  Optics=UMaterialInstanceDynamic::Create(Beam->LightFunctionMaterial,this);
  Beam->SetLightFunctionMaterial(Optics);
 }
 // A very local bounce reveals the casing without lighting the room.
 HandFill=NewObject<UPointLightComponent>(Character,TEXT("TorchHandBounce"));
 HandFill->SetupAttachment(HeldRoot);HandFill->SetRelativeLocation(FVector(29,9,-3));
 HandFill->SetIntensityUnits(ELightUnits::Lumens);HandFill->SetIntensity(0.003f);
 HandFill->SetAttenuationRadius(22);HandFill->SetCastShadows(false);
 HandFill->SetIndirectLightingIntensity(0);HandFill->SetVolumetricScatteringIntensity(0);
 HandFill->SetLightColor(FLinearColor(0.80f,0.86f,1.0f));HandFill->RegisterComponent();
 Focus=TargetFocus=FMath::Clamp(InitialFocus,0.0f,1.0f);
 PreviousCapsuleLocation=Character->GetActorLocation();SmoothedGroundZ=PreviousCapsuleLocation.Z;
 PreviousAim=Character->GetControlRotation();UpdateBeam();
}

void UStationPlayerPresentationComponent::AdjustFocus(float Steps)
{
 if(FMath::IsFinite(Steps))SetFocus(TargetFocus+Steps*0.1f);
}

void UStationPlayerPresentationComponent::SetFocus(float Value)
{
 if(FMath::IsFinite(Value))TargetFocus=FMath::Clamp(Value,0.0f,1.0f);
}

void UStationPlayerPresentationComponent::UpdateBeam()
{
 if(!Beam)return;
 // Lumen units concentrate the same available flux as the cone narrows.
 Beam->SetOuterConeAngle(FMath::Lerp(34.0f,11.0f,Focus));
 Beam->SetInnerConeAngle(0.0f);
 Beam->SetAttenuationRadius(FMath::Lerp(1800.0f,6000.0f,Focus));
 Beam->SetIntensity(FMath::Lerp(WideLumens,FocusedLumens,Focus));
 if(Optics)Optics->SetScalarParameterValue(TEXT("Focus"),Focus);
}

void UStationPlayerPresentationComponent::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
 Super::TickComponent(Dt,TickType,TickFunction);
 if(!Character || !Camera || !Beam || !Character->IsLocallyControlled() || Dt<=0)return;
 const float Blend=1.0f-FMath::Exp(-10.0f*Dt);
 const APlayerController* PC=Cast<APlayerController>(Character->GetController());
 // Release also follows physical input state, so a missed release or ignored look cannot latch zoom.
 const bool bInspect=bInspectRequested && PC && PC->IsInputKeyDown(EKeys::RightMouseButton) && !PC->IsLookInputIgnored();
 InspectAmount=FMath::Lerp(InspectAmount,bInspect?1.0f:0.0f,1.0f-FMath::Exp(-8.0f*Dt));
 if(FMath::Abs(InspectAmount-(bInspect?1.0f:0.0f))<0.0001f)InspectAmount=bInspect?1.0f:0.0f;
 const float NewFocus=FMath::Lerp(Focus,TargetFocus,Blend);
 if(FMath::Abs(NewFocus-Focus)>0.00001f){Focus=NewFocus;UpdateBeam();}
 HandFill->SetVisibility(Beam->IsVisible());
 const FVector Velocity=Character->GetVelocity();
 const float Speed=Velocity.Size2D();
 const bool Grounded=Character->GetCharacterMovement()->IsMovingOnGround();
 const FVector CapsuleLocation=Character->GetActorLocation();
 const float MaxOffset=Character->GetCharacterMovement()->MaxStepHeight*0.8f;
 const bool ResetHeight=!Grounded || !bWasGrounded || Dt>0.15f ||
  FVector::DistSquared(CapsuleLocation,PreviousCapsuleLocation)>FMath::Square(150.0f);
 if(ResetHeight){SmoothedGroundZ=CapsuleLocation.Z;GroundZVelocity=0;}
 else
 {
  // Exact critically damped spring response for this frame's target height.
  // Removes tread-sized view jolts without a ramp over the walking collision.
  const float Omega=FMath::Clamp(GroundHeightResponse,6.0f,40.0f);
  const double Error=SmoothedGroundZ-CapsuleLocation.Z;
  const double Travel=(GroundZVelocity+Omega*Error)*Dt;
  const double Decay=FMath::Exp(-Omega*Dt);
  SmoothedGroundZ=CapsuleLocation.Z+(Error+Travel)*Decay;
  GroundZVelocity=(GroundZVelocity-Omega*Travel)*Decay;
  SmoothedGroundZ=FMath::Clamp(SmoothedGroundZ,CapsuleLocation.Z-MaxOffset,CapsuleLocation.Z+MaxOffset);
 }
 const float GroundOffset=SmoothedGroundZ-CapsuleLocation.Z;
 const FVector LocalGroundOffset=Camera->GetComponentQuat().UnrotateVector(FVector(0,0,GroundOffset));
 const float StairBob=FMath::Lerp(1.0f,0.35f,FMath::Clamp(FMath::Abs(GroundOffset)/4.0f,0.0f,1.0f));
 PreviousCapsuleLocation=CapsuleLocation;
 const float Run=FMath::Clamp((Speed-350.0f)/250.0f,0.0f,1.0f);
 const float TargetMotion=Grounded?FMath::Clamp(Speed/150.0f,0.0f,1.0f):0.0f;
 MotionWeight=FMath::Lerp(MotionWeight,TargetMotion,Blend);
 IdleWeight=FMath::Lerp(IdleWeight,Grounded?1.0f-MotionWeight:0.0f,Blend);
 // Independent slow rhythms avoid a rigid loop; all offsets stay centered, never accumulating aim drift.
 BreathTime+=FMath::Min(Dt,0.05f);
 const float Breath=FMath::Sin(BreathTime*2.0*PI*0.22);
 const float Balance=0.75f*FMath::Sin(BreathTime*2.0*PI*0.13)+0.25f*FMath::Sin(BreathTime*2.0*PI*0.31+0.7);
 const float IdleAmount=IdleWeight*IdleSwayScale*HeadBobScale;
 const FVector IdleOffset=FVector(0.05f*Breath,0.20f*Balance,0.30f*Breath)*IdleAmount;
 const FRotator IdleRotation(0.055f*Breath*IdleAmount,0.065f*Balance*IdleAmount,0.035f*Balance*IdleAmount);
 if(Grounded && Speed>5)Phase=FMath::Fmod(Phase+Speed*Dt/190.0f*2.0f*PI,4.0f*PI);
 if(Grounded && !bWasGrounded)LandingOffset=-FMath::Clamp(-PreviousVerticalSpeed/450.0f,0.0f,1.6f);
 LandingOffset=FMath::Lerp(LandingOffset,0.0f,Blend);
 const float Step=FMath::Sin(Phase),Sway=FMath::Sin(Phase*0.5f);
 const float GaitAmount=MotionWeight*HeadBobScale*StairBob;
 ViewOffset=FVector(0,FMath::Lerp(WalkSwayCm,RunSwayCm,Run)*Sway,(1.05f+0.6f*Run)*Step)*GaitAmount+IdleOffset+LocalGroundOffset;
 ViewOffset.Z+=LandingOffset*HeadBobScale;
 Camera->ClearAdditiveOffset();
 const FRotator GaitRotation(0.10f*Step*GaitAmount,(0.06f+0.04f*Run)*Sway*GaitAmount,(0.10f+0.08f*Run)*Sway*GaitAmount);
 const float InspectFovOffset=-FMath::Clamp(InspectFovReduction,0.0f,FMath::Max(0.0f,Camera->FieldOfView-40.0f))*InspectAmount;
 Camera->AddAdditiveOffset(FTransform(GaitRotation+IdleRotation,ViewOffset),InspectFovOffset);
 const FRotator Aim=Character->GetControlRotation();
 FVector2D TargetLag(FMath::Clamp(FMath::FindDeltaAngleDegrees(PreviousAim.Yaw,Aim.Yaw)/Dt*-0.006f,-2.2f,2.2f),FMath::Clamp(FMath::FindDeltaAngleDegrees(PreviousAim.Pitch,Aim.Pitch)/Dt*-0.006f,-1.8f,1.8f));
 AimLag=FMath::Lerp(AimLag,TargetLag,Blend);
 // Camera additive offsets affect the rendered view, not attached component transforms.
 // Follow that view exactly, then add restrained hand movement in view-local space.
 // Without this, stronger camera sway makes a nearly stationary torch swim across the frame.
 const float HandScale=FMath::Clamp(HeldMotionScale,0.0f,1.0f);
 const FVector HandOffset=(FVector(0,(0.45f+0.35f*Run)*Sway,0.5f*Step+LandingOffset)*MotionWeight*StairBob
  +FVector(0,0.08f*Balance,0.10f*Breath)*IdleWeight)*HandScale;
 const FRotator HandRotation=FRotator(AimLag.Y+0.45f*Step*MotionWeight,AimLag.X+0.3f*Sway*MotionWeight,0.4f*Sway*MotionWeight)*HandScale;
 const FTransform ViewTransform(GaitRotation+IdleRotation,ViewOffset);
 HeldRoot->SetRelativeTransform(FTransform(HandRotation,HandOffset)*ViewTransform);
 PreviousAim=Aim;PreviousVerticalSpeed=Velocity.Z;bWasGrounded=Grounded;
}

void UStationPlayerPresentationComponent::EndPlay(const EEndPlayReason::Type Reason)
{
 if(Camera)Camera->ClearAdditiveOffset();
 Super::EndPlay(Reason);
}
