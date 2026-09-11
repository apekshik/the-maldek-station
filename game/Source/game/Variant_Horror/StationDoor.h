#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationDoor.generated.h"

class UStaticMeshComponent;
class UBoxComponent;
class UTextRenderComponent;
class UWidgetComponent;
class APlayerController;
class APawn;
class UMaterialInstanceDynamic;
class UMaterialInterface;
class UCameraComponent;
class UMeshComponent;
class UAudioComponent;
class USpotLightComponent;
class USoundBase;
class SWidget;
class STextBlock;
 class UStationPlayerPresentationComponent;

/** Hinged station door. Locked doors never change their collision or opening target. */
UCLASS(Blueprintable)
class GAME_API AStationDoor : public AActor
{
 GENERATED_BODY()
public:
 AStationDoor();
 virtual void OnConstruction(const FTransform& Transform) override;
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 UFUNCTION(BlueprintCallable, Category="Door") void CancelKeypadInteraction();
 UFUNCTION(BlueprintPure, Category="Door") bool IsUsingKeypad() const { return bEnteringCode; }
 UFUNCTION(BlueprintPure, Category="Door|Key") bool IsUsingKey() const { return bUsingKey; }
 UFUNCTION(BlueprintPure, Category="Door|Key") float GetKeyInsertion() const { return KeyInsertion; }
 UFUNCTION(BlueprintPure, Category="Door|Key") FVector GetKeyGripWorldPosition(float Insertion) const;
 UFUNCTION(BlueprintPure, Category="Door") FVector GetKeypadButtonWorldPosition(int32 Index) const;
 UFUNCTION(BlueprintCallable, Category="Door") bool TryInteract();
 UFUNCTION(BlueprintCallable, Category="Door") bool Unlock();
 UFUNCTION(BlueprintCallable, Category="Door") bool Lock();
 UFUNCTION(BlueprintCallable, Category="Door") bool SubmitCode(const FString& Code);
 UFUNCTION(BlueprintPure, Category="Door") bool IsLocked() const { return bLocked; }
 UFUNCTION(BlueprintPure, Category="Door") float GetOpenAngle() const { return CurrentAngle; }
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<USceneComponent> DoorRoot;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<USceneComponent> Hinge;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> Leaf;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> Glass;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> FixedHardware;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> Keypad;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> InteriorElectronics;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> ElectronicStrike;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Authored") TObjectPtr<UStaticMeshComponent> FrontLever;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Authored") TObjectPtr<UStaticMeshComponent> BackLever;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Authored") TObjectPtr<UStaticMeshComponent> MovingLatch;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Authored") TObjectPtr<UStaticMeshComponent> BottomSeal;
 /** Opt-in for fitted assemblies; legacy doors retain their original layout. */
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Authored") bool bUseAuthoredHardware=false;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Authored") FVector AuthoredKeyLocation=FVector(114.6,-3.5,100);
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Authored") FRotator AuthoredKeyRotation=FRotator::ZeroRotator;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Authored") float KeyFaceDepth=4.6f;
  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Authored") bool bInteriorIsNegativeY=true;
  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Authored") float AuthoredLeverAngle=25.f;
  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Privacy") bool bHasPrivacyLatch=false;
  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Privacy") FVector PrivacyBoltLocation=FVector::ZeroVector;
  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Privacy") TObjectPtr<UStaticMeshComponent> PrivacyIndicator;
  UFUNCTION(BlueprintCallable, Category="Door|Privacy") bool TryTogglePrivacy();
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Key") TObjectPtr<USceneComponent> KeyLockRoot;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Key") TObjectPtr<UStaticMeshComponent> KeyHousing;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Key") TObjectPtr<UStaticMeshComponent> KeyPlug;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Key") TObjectPtr<UStaticMeshComponent> InteriorKeyPlug;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Key") TObjectPtr<UStaticMeshComponent> ServiceKey;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door|Key") TObjectPtr<USpotLightComponent> KeyInspectionLight;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UBoxComponent> LeafCollision;
 UPROPERTY(VisibleAnywhere, Category="Door") TObjectPtr<UTextRenderComponent> Prompt;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UWidgetComponent> InteractionPrompt;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UMaterialInterface> InteractionPromptMaterial;
 UPROPERTY(VisibleAnywhere, Category="Door") TObjectPtr<UTextRenderComponent> KeypadDisplay;
 UPROPERTY(VisibleAnywhere, Category="Door") TObjectPtr<UCameraComponent> KeypadCamera;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door|Key") FVector KeyCameraOffset=FVector(18,35,14);
 /** Interaction framing and side glances can be tuned independently. */
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Peek", meta=(ClampMin="40",ClampMax="100")) float KeyCloseupFOV=56.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Peek", meta=(ClampMin="40",ClampMax="100")) float KeypadCloseupFOV=64.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Peek", meta=(ClampMin="0",ClampMax="120")) float PeekYawDegrees=95.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Peek", meta=(ClampMin="0",ClampMax="15")) float PeekRollDegrees=8.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Peek", meta=(ClampMin="40",ClampMax="110")) float PeekFOV=85.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Peek", meta=(ClampMin="1",ClampMax="20")) float PeekResponse=9.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") bool bHasKeypad=false;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Key") bool bHasKeyLock=false;
 /** Temporary possession gate. Future inventory can supply this per required key. */
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Key") bool bKeyAvailable=true;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Key") FName RequiredKeyId=TEXT("StationService");
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") bool bLocked=false;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door") bool bRelockOnClose=true;
 /** Empty by default: a level designer must deliberately configure a code. */
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") FString AccessCode;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door") float OpenAngle=105.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door", meta=(ClampMin="10")) float DegreesPerSecond=85.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door", meta=(ClampMin="50")) float InteractionDistance=220.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> ButtonSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> ClearSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> ConfirmSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> RejectSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> UnlatchSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> MovementSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> CloseSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> UnlockSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> LockSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> KeyTurnSound;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Audio", meta=(ClampMin="0",ClampMax="8")) float KeyTurnVolume=4.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> ClosingMovementSound;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Audio", meta=(ClampMin="0",ClampMax="4")) float KeypadVolume=1.6f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Audio", meta=(ClampMin="0",ClampMax="4")) float DoorVolume=1.3f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door|Audio", meta=(ClampMin="0",ClampMax="4")) float MovementVolume=1.2f;
 UPROPERTY(VisibleAnywhere, Category="Door|Audio") TObjectPtr<UAudioComponent> EventAudio;
 UPROPERTY(VisibleAnywhere, Category="Door|Audio") TObjectPtr<UAudioComponent> MotionAudio;
 UPROPERTY(VisibleAnywhere, Category="Door|Audio") TObjectPtr<UAudioComponent> KeypadAudio;
 UPROPERTY(VisibleAnywhere, Category="Door|Audio") TObjectPtr<UAudioComponent> LockAudio;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door|Audio") TArray<TObjectPtr<USoundBase>> OpeningTakes;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door|Audio") TArray<TObjectPtr<USoundBase>> ClosingTakes;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door|Audio") TArray<TObjectPtr<USoundBase>> CloseImpactTakes;
private:
 bool bMotionWasActive=false;
 float HardwareReleaseRemaining=0.f;
 float LeverDepression=0.f;
 FVector LatchRest=FVector::ZeroVector,SealRest=FVector::ZeroVector;
 TSharedPtr<SWidget> HintWidget;
 TSharedPtr<STextBlock> HintAction,HintDetail,HintKey;
 void ShowDoorHint(bool bVisible,const FString& Action=FString(),const FString& Detail=FString());
 UPROPERTY(Transient) TObjectPtr<USoundBase> ActiveTravelSound;
 TWeakObjectPtr<USoundBase> LastOpeningTake,LastClosingTake,LastImpactTake;
 void PlayDoorSound(USoundBase* Sound,bool bKeypad=false);
 float CurrentAngle=0.f;
 float TargetAngle=0.f;
 float FeedbackSeconds=0.f;
 bool bObstructed=false;
 bool bEnteringCode=false;
 bool bUsingKey=false;
 bool bDraggingKey=false;
 bool bKeyMouseWasDown=false;
 float KeyInsertion=0.f;
 float KeyTurnElapsed=-1.f;
 FVector2D LastDragMouse=FVector2D::ZeroVector;
 FRotator CloseupRestRotation=FRotator::ZeroRotator;
 float PeekAmount=0.f;
 float CloseupRestFOV=56.f;
 float CloseupFacingYaw=0.f;
 bool bPeekingAway=false;
 TWeakObjectPtr<USpotLightComponent> PeekBeam;
 TWeakObjectPtr<USceneComponent> PeekBeamParent;
 TWeakObjectPtr<UStationPlayerPresentationComponent> PeekPresentation;
 FName PeekBeamSocket;
 FTransform PeekBeamRest=FTransform::Identity;
 FVector2D PeekMouseOrigin=FVector2D::ZeroVector;
 void EndPeekBeam();
 bool bPeekReady=false;
 void TickCloseupPeek(float DeltaSeconds,APlayerController* Controller);
 bool BeginKeyInteraction(APlayerController* Controller);
 void BeginCloseup(APlayerController* Controller);
 void TickKeyInteraction(float DeltaSeconds,APlayerController* Controller);
 void UpdateKeyPose(float TurnDegrees=0.f,float Withdrawal=0.f);
 bool bCodeRejected=false;
 FTimerHandle LockSoundTimer;
 FString EnteredCode;
 float KeypadBlendRemaining=0;
 TWeakObjectPtr<APlayerController> KeypadController;
 TWeakObjectPtr<AActor> PreviousViewTarget;
 TWeakObjectPtr<APawn> PreviousPawn;
 TArray<TWeakObjectPtr<UMeshComponent>> HiddenPlayerMeshes;
 bool bPreviousMouseCursor=false;
 uint8 PreviousMovementMode=0, PreviousCustomMovementMode=0;
 bool BeginKeypadInteraction(APlayerController* Controller);
 void EndKeypadInteraction(bool bBlend);
 void PressKeypadButton(int32 Index);
 int32 HoveredKeypadButton(APlayerController* Controller) const;
 UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> StatusMaterial;
 UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> PrivacyMaterial;
 bool HasPrivacyBoltFocus(APlayerController* Controller) const;
 bool HasFocus(APlayerController* Controller) const;
 bool IsInteriorSide(APlayerController* Controller) const;
 bool CanOccupyAngle(float Angle) const;
 void RefreshLockVisuals();
};
