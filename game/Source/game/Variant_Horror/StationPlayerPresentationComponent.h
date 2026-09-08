#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "StationPlayerPresentationComponent.generated.h"

class ACharacter;
class UCameraComponent;
class USceneComponent;
class USpotLightComponent;
class UPointLightComponent;
class UMaterialInstanceDynamic;
class UStaticMesh;

/** Camera and held-tool presentation. Never moves the collision capsule. */
UCLASS(ClassGroup=(Station), meta=(BlueprintSpawnableComponent))
class GAME_API UStationPlayerPresentationComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UStationPlayerPresentationComponent();
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

 UFUNCTION(BlueprintCallable, Category="Flashlight") void AdjustFocus(float Steps);
 UFUNCTION(BlueprintCallable, Category="Flashlight") void SetFocus(float Value);
 UFUNCTION(BlueprintPure, Category="Flashlight") float GetFocus() const { return Focus; }
 UFUNCTION(BlueprintPure, Category="Flashlight") float GetTargetFocus() const { return TargetFocus; }
 UFUNCTION(BlueprintPure, Category="Walking") FVector GetViewOffset() const { return ViewOffset; }
 UFUNCTION(BlueprintCallable, Category="Looking") void SetInspectActive(bool bActive) { bInspectRequested=bActive; }
 UFUNCTION(BlueprintPure, Category="Looking") float GetInspectAmount() const { return InspectAmount; }
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Looking", meta=(ClampMin="0",ClampMax="20")) float InspectFovReduction=12.0f;

 /** Scales breathing and gait motion; zero removes voluntary sway but retains stair smoothing. */
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walking", meta=(ClampMin="0",ClampMax="1.5")) float HeadBobScale=0.7f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walking", meta=(ClampMin="0",ClampMax="8")) float IdleSwayScale=1.0f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walking", meta=(ClampMin="0",ClampMax="3")) float WalkSwayCm=0.9f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walking", meta=(ClampMin="0",ClampMax="3")) float RunSwayCm=1.65f;
 /** Critically damped ground-height response; never changes capsule collision. */
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Walking", meta=(ClampMin="6",ClampMax="40")) float GroundHeightResponse=18.0f;
 UPROPERTY(EditAnywhere, Category="Flashlight", meta=(ClampMin="0",ClampMax="1")) float InitialFocus=0.35f;
 UPROPERTY(EditAnywhere, Category="Flashlight") float WideLumens=1.2f;
 UPROPERTY(EditAnywhere, Category="Flashlight") float FocusedLumens=1.35f;
 UPROPERTY(EditAnywhere, Category="Flashlight") TObjectPtr<UStaticMesh> DetailedTorchMesh;
 /** Independent hand motion relative to the rendered view; does not scale camera sway. */
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Flashlight", meta=(ClampMin="0",ClampMax="1")) float HeldMotionScale=0.15f;

private:
 UPROPERTY(Transient) TObjectPtr<ACharacter> Character;
 UPROPERTY(Transient) TObjectPtr<UCameraComponent> Camera;
 UPROPERTY(Transient) TObjectPtr<USpotLightComponent> Beam;
 UPROPERTY(Transient) TObjectPtr<USceneComponent> HeldRoot;
 UPROPERTY(Transient) TObjectPtr<UPointLightComponent> HandFill;
 UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> Optics;
 float Focus=0.35f,TargetFocus=0.35f,Phase=0,MotionWeight=0,LandingOffset=0,PreviousVerticalSpeed=0;
 bool bWasGrounded=true;
 FRotator PreviousAim=FRotator::ZeroRotator;
 FVector2D AimLag=FVector2D::ZeroVector;
 FVector ViewOffset=FVector::ZeroVector;
 double SmoothedGroundZ=0;
 double BreathTime=0;
 float IdleWeight=0;
 bool bInspectRequested=false;
 float InspectAmount=0;
 float GroundZVelocity=0;
 FVector PreviousCapsuleLocation=FVector::ZeroVector;
 void UpdateBeam();
};
