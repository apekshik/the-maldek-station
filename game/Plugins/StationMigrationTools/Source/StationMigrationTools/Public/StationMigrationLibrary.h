#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "StationMigrationLibrary.generated.h"
class UMaterialInterface;

UCLASS()
class STATIONMIGRATIONTOOLS_API UStationMigrationLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // Changes the render target, independent of desktop window borders. Only PIE is eligible.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static bool SetPIERenderSize(int32 Width, int32 Height);

    // Raw engine measurements; enable stat unit before sampling. Missing values stay absent.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static TMap<FString, double> CapturePIEFrameStats();

    // Wait for shader compilation and return real compile errors from the active RHI resources.
    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static TArray<FString> ValidateMaterialShaders(const TArray<UMaterialInterface*>& Materials);

    UFUNCTION(BlueprintCallable, Category="Station Validation")
    static TArray<FString> GetLandscapeHeightmapPaths(AActor* LandscapeActor);
};
